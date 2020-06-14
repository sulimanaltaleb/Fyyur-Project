# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, \
    flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from sqlalchemy import func
from flask_wtf import *
from wtforms import *
from datetime import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref="Venue", lazy=True)

    # TODO: implement any missing fields, as a database
    # migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref="Artist", lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime)

# TODO:implement any missing fields,
# as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships
# and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based
    # on number of upcoming shows per venue.
    data = []
    venues_location = db.session.query(Venue.city, Venue.state).distinct()
    for venue in venues_location:
        filtered_venues = Venue.query.filter_by(
            state=venue.state).filter_by(city=venue.city).all()
        venuesPerEachCity = []
        for venue in filtered_venues:
            venuesPerEachCity.append({
                "id": venue.id,
                "name": venue.name,
                "upcoming_shows": len(db.session.query(Show)
                                      .filter(Show.venue_id == venue.id)
                                      .filter(Show.start_time > datetime.now())
                                      .all())
            })

        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": venuesPerEachCity
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop"
    # and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    results = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    data = []
    for r in results:
        data.append({
            "id": r.id,
            "name": r.name,
            "upcoming_shows": len(db.session.query(Show)
                                    .filter(Show.venue_id == r.id)
                                    .filter(Show.start_time > datetime.now())
                                    .all())
        })

    response = {
        "count": len(results),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    try:

        venue = Venue.query.get(venue_id)
        data = []
        upcoming = '''db.session.query(Show).join(Artist)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time > datetime.now()).all()'''
        upcomingShows = []

        past = ''' db.session.query(Show).join(Artist)
        .filter(Show.venue_id == venue_id)
        .filter(Show.start_time < datetime.now()).all()'''
        pastShows = []

        for u in upcoming:
            upcomingShows.append({
                "artist_id": u.Artist.id,
                "artist_name": u.Artist.name,
                "artist_image_link": u.Artist.image_link,
                "start_time": u.start_time.strftime("%Y-%m-%d, %H:%M:%S")
            })

        for p in past:
            pastShows.append({
                "artist_id": p.Artist.id,
                "artist_name": p.Artist.name,
                "artist_image_link": p.Artist.image_link,
                "start_time": p.start_time.strftime("%Y-%m-%d, %H:%M:%S")
            })

        data = [{
            "id": venue.id,
            "name": venue.name,
            "genres": (venue.genres),
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": pastShows,
            "upcoming_shows": upcomingShows,
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming)
        }]

        data = list(filter(lambda d: d['id'] == venue_id, data))[0]
        return render_template('pages/show_venue.html', venue=data)
    except:
        abort(404)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    data = request.form
    try:
        name = VenueForm().name.data
        city = VenueForm().city.data
        state = VenueForm().state.data
        address = VenueForm().address.data
        phone = VenueForm().phone.data
        genres = ','.join(VenueForm().genres.data)
        facebook_link = VenueForm().facebook_link.data
        website = VenueForm().website.data
        image_link = VenueForm().image_link.data
        seeking_talent = VenueForm().seeking_talent.data
        seeking_description = VenueForm().seeking_description.data

        venue = Venue(name=name, city=city, state=state, address=address,
                      phone=phone, image_link=image_link,
                      facebook_link=facebook_link,
                      website=website, seeking_talent=seeking_talent,
                      seeking_description=seeking_description, genres=genres)
        db.session.add(venue)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name +
    # ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
        else:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases
    # where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on
    # a Venue Page, have it so that
    # clicking that button delete it from the db then
    # redirect the user to the homepage
    # return None


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    Art = Venue.query.get(venue_id)
    form = ArtistForm(obj=Art)
    if form.validate_on_submit():
        form.populate_obj(Art)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=Art)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venEdit = Venue.query.get(venue_id)

    venEdit.name = form.name.data
    venEdit.genres = form.genres.data
    venEdit.city = form.city.data
    venEdit.state = form.state.data
    venEdit.phone = form.phone.data
    venEdit.website = form.website.data
    venEdit.facebook_link = form.facebook_link.data
    venEdit.seeking_talent = form.seeking_talent.data
    venEdit.seeking_description = form.seeking_description.data
    venEdit.image_link = form.image_link.data
    venEdit.address = form.address.data
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial
    # string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals",
    # "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    searchResults = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    data = []
    for artist in searchResults:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(db.session.query(Show)
                                      .filter(Show.artist_id == artist.id)
                                      .filter(Show.start_time > datetime
                                      .now()).all())
        })

    response = {
        "count": len(searchResults),
        "data": data
    }
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    try:
        artist = Artist.query.get(artist_id)
        upcoming = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist_id).filter(
                Show.start_time > datetime.now()).all()
        upcomingShows = []
        past = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist_id).filter(
                Show.start_time < datetime.now()).all()
        pastShows = []

        for u in upcoming:
            upcomingShows.append({
                "venue_id": u.Venue.id,
                "venue_name": u.Venue.name,
                "venue_image_link": u.Venue.image_link,
                "start_time": (u.start_time.strftime("%Y-%m-%d, %H:%M:%S"))
            })

        for p in past:
            pastShows.append({
                "venue_id": p.Venue.id,
                "venue_name": p.Venue.name,
                "venue_image_link": p.Venue.image_link,
                "start_time": (p.start_time.strftime("%Y-%m-%d, %H:%M:%S"))
            })

        data = [{
            "id": artist.id,
            "name": artist.name,
            "genres": (artist.genres),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": pastShows,
            "upcoming_shows": upcomingShows,
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming)
        }]

        data = list(filter(lambda d: d['id'] == artist_id, data))[0]
        return render_template('pages/show_artist.html', artist=data)
    except:
        abort(404)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form = ArtistForm(obj=artist)
    if form.validate_on_submit():
        form.populate_obj(artist)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website = form.website.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        name = ArtistForm().name.data
        city = ArtistForm().city.data
        state = ArtistForm().state.data
        address = ArtistForm().address.data
        phone = ArtistForm().phone.data
        genres = ','.join(ArtistForm().genres.data)
        facebook_link = ArtistForm().facebook_link.data
        website = ArtistForm().website.data
        image_link = ArtistForm().image_link.data
        seeking_venue = ArtistForm().seeking_venue.data
        seeking_description = ArtistForm().seeking_description.data
        newArtist = Artist(name=name, city=city, genres=genres, state=state,
                           phone=phone, image_link=image_link,
                           facebook_link=facebook_link, website=website,
                           seeking_venue=seeking_venue,
                           seeking_description=seeking_description)
        db.session.add(newArtist)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' +
    # data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based
    # on number of upcoming shows per venue.
    shows = Show.query.all()
    data = []
    for i in shows:
        ven = Venue.query.filter_by(id=i.venue_id).first()
        art = Artist.query.filter_by(id=i.artist_id).first()
        data.append({
            "venue_id": i.venue_id,
            "venue_name": ven.name,
            "artist_id": i.artist_id,
            "artist_name": art.name,
            "artist_image_link": art.image_link,
            "start_time": (i.start_time.strftime("%Y-%m-%d, %H:%M:%S"))
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db,
    # upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        # show = Show()
        artist_id = ShowForm().artist_id.data
        venue_id = ShowForm().venue_id.data
        time = ShowForm().start_time.data
        start_time = time.strftime("%Y-%m-%d, %H:%M:%S")
        newShow = Show(artist_id=artist_id, venue_id=venue_id,
                       start_time=start_time)
        db.session.add(newShow)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
        abort(404)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            # on successful db insert, flash success
            flash('Show was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(''' % (asctime) s % (levelname) s : % (message)s
                  [in % (pathname) s : % (lineno)d]''')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
