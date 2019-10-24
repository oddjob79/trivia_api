import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def get_category_list():
    # get full list of categories
    categories = Category.query.order_by(Category.id).all()
    # declare list for storing categories
    catlist = []
    # loop through categories and append the id and type to the list
    for cat in categories:
        catlist.append({
            cat.id:cat.type
        })

    return catlist

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

  @app.route('/api/categories/<string:category>/questions')
  def retrieve_questions(category):
    # # get full list of categories
    # categories = Category.query.order_by(Category.id).all()
    # # declare list for storing categories
    # catlist = []
    # # loop through categories and append the id and type to the list
    # for cat in categories:
    #     catlist.append({
    #         cat.id:cat.type
    #     })
    #
    if category == 'all':
        selection = Question.query.order_by(Question.id).all()
    else:
        # Need to do this in a round about way, as no table relationship on category_id
        # query the categories table to find the id of the category
        selected_cat = Category.query.filter(Category.type.ilike(category)).one_or_none()
        selection = Question.query.filter(Question.category==selected_cat.id).order_by(Question.id).all()

    current_questions = paginate_questions(request, selection)
    catlist = get_category_list()

    if current_questions is None:
      abort(404) # TODO - REQUIRE specific error message here
    else:
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(current_questions),
        'current_category': category,
        'categories': catlist
      })

  @app.route('/api/categories')
  def retrieve_categories():
      selection = Category.query.order_by(Category.id).all()
      current_categories = [category.format() for category in selection]

      if current_categories is None:
          abort(404) # TODO - REQUIRE specific error message here
      else:
          return jsonify({
            'success': True,
            'categories': current_categories,
            'total_categories': len(current_categories)
          })

  @app.route('/api/questions', methods=['POST'])
  def create_question():

      new_question = request.json.get('question', None)
      new_answer = request.json.get('answer', None)
      new_category = request.json.get('category', None)
      new_difficulty = request.json.get('difficulty', None)

      new_category = Category.query.filter(Category.type.ilike(new_category)).one_or_none()

      try:
          question = Question(question=new_question, answer=new_answer, category=new_category.id, difficulty=new_difficulty)
          question.insert()

          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify({
              'success': True,
              'created': new_question,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
          })
      except:
          abort(422)

  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
          question = Question.query.filter(Question.id==question_id).one_or_none()

          if question is None:
              abort(404)

          question.delete()
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify({
              'success': True,
              'deleted': str(question_id) + ' - ' + question.question,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
          })
      except:
          abort(422)







  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app
