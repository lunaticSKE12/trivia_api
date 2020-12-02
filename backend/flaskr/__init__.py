import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resource={'/': {'origins': '*'}})

    '''
  Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if(len(categories_dict) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    '''
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        total_question = len(selection)
        current_questions = paginate_question(request, selection)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if(len(categories_dict) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'question': current_questions,
            'total_questions': total_question,
            'categories': categories_dict
        })

    '''
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()

            if(question is None):
                abort(404)

            question.delete()
            return jsonify({
                'sucess': True,
                'deleted': id
            })

        except:
            abort(422)

    '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()

        if((new_answer is None) or (new_category is None) or (new_difficulty is None) or (new_question is None)):
            abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id.all())
            current_questions = paginate_question(request, selection)

            return jsonify({
                'success': True,
                'created': question.id
            })

        except:
            abort(422)

    '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('question/search', methods=["POST"])
    def search_question():
        body = request.get_json()

        if(body.get('searchTerm')):
            search = body.get('searchTerm')

            selection = Question.query.filter(
                Question.question.ilike(f'%{searchTerm}%')).all()

            if(len(selection) == 0):
                abort(404)

            paginate = paginate_question(request, selection)

            return jsonify({
                'success': True,
                'questions': paginate,
                'total_questions': len(Question.query.all())
            })
    '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:id>/questions')
    def get_question_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        if(category is None):
            abort(404)

        selection = Question.query.filter_by(category=category.id).all()

        paginate = paginate_question(request, selection)

        return jsonify({
            'success': True,
            'questions': paginate,
            'total_question': len(Question.query.all()),
            'current_category': category.type
        })

    '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:
            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            prev = body.get('previous_questions')
            category = body.get('quiz_category')

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((prev))).all()
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((prev))).all()

            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })

        except:
            abort(422)

    '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    return app
