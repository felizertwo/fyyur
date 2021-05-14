#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
import dateutil.parser
from datetime import datetime
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import config
from model import Venue, Artist, Show, db


app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
    locations = set()

    for venue in venues:
        locations.add((venue.city, venue.state))

    for location in locations:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
        })

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # get current date
        current_date = datetime.now()

        for show in shows:
            if show.start_time > current_date:
                num_upcoming_shows += 1

        for venue_location in data:
            if venue.state == venue_location['state'] and venue.city == venue_location['city']:
                venue_location['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    query=Venue.query
    for s in re.split(',| ', search_term):
        if s:
            query = query.filter(
                Venue.name.ilike(f'%{s}%') 
                | Venue.state.ilike(f'%{s}%') 
                | Venue.city.ilike(f'%{s}%')
            )
    
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    response = {
        "count": query.count(),
        "data": query
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in venue.shows:
        data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    
    if not form.validate():
        for field, errors in form.errors.items():
            flash(field + ': ' + errors[0])
        return render_template('forms/new_venue.html', form=form)
    try:
        # get form data and create
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        # flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Venue' +
              request.form['name'] + ' could not be listed')
    finally:
        # closes session
        db.session.close()
    return render_template('pages/home.html')


#---------- Edit Venue is missing --------------#
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        name = form.name.data
        
        venue.name = name
        venue.city = form.city.data
        venue.state = form.state.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website = form.website.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        if not form.validate():
            for field, errors in form.errors.items():
                flash(field + ': ' + errors[0])
            
            return render_template('forms/edit_venue.html', form=form, venue=venue)
        
        db.session.commit()
        flash('Venue ' + name + 'has been updated')
    except:
        db.session.rollback()
        flash('An error occured while trying to update Venue')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # Get venue by ID
        venue = Venue.query.get(venue_id)
        venue_name = venue.name

        db.session.delete(venue)
        db.session.commit()

        flash('Venue ' + venue_name + ' was deleted')
    except:
        flash(' an error occured and Venue ' + venue_name + ' was not deleted')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = []

    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query=Artist.query
    for s in re.split(',| ', search_term):
        if s:
            query = query.filter(
                Artist.name.ilike(f'%{s}%') 
                | Artist.state.ilike(f'%{s}%') 
                | Artist.city.ilike(f'%{s}%')
            )

    response = {
        'count': query.count(),
        'data': query
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in artist.shows:
        data = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data) 

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'facebook_link': artist.facebook_link,
        'website_link': artist.website_link,
        'image_link': artist.image_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.genres.default = artist.genres
    form.state.default = artist.state
    form.process()

    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    try:
        form = ArtistForm()
        
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.phone = form.phone.data
        artist.state = form.state.data
        artist.city = form.city.data
        artist.genres = form.genres.data
        artist.website_link = form.website_link.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        if not form.validate():
            for field, errors in form.errors.items():
                flash(field + ': ' + errors[0])
            return render_template('forms/edit_artist.html', form=form, artist=artist)

        db.session.commit()
        flash('The Artist ' +
              request.form['name'] + ' has been successfully updated!')
    except:
        db.session.rollback()
        flash('An Error has occured and the update unsuccessfull')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    if not form.validate():
        for field, errors in form.errors.items(): 
            flash(field + ': ' + errors[0])
        return render_template('forms/new_artist.html', form=form)
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error ocurred, Artist ' +
              request.form['name'] + ' could not be listed')
    finally:
        db.session.close()

    return render_template('pages/home.html')

# Delete Artists
# Open ToDo


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.order_by(db.desc(Show.start_time))

    data = []
    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        show = Show()
        form.populate_obj(show)

        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occured. show could not be listed')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
