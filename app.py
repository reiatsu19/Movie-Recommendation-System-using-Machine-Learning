import pickle
import streamlit as st
import requests
from googletrans import Translator

import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()


def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    data = c.fetchall()
    if len(data) == 0:
        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
        conn.commit()
        return True
    else:
        return False


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM userstable WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        return True
    else:
        return False


# Initialize the translator
translator = Translator()


def translate_to_malay(text, lang):
    translation = translator.translate(text, dest='ms' if lang == 'Malay' else lang)
    return translation.text


def translate_to_chinese(text, lang):
    translation = translator.translate(text, dest='zh-CN' if lang == 'Chinese' else lang)
    return translation.text


def translate_to_tamil(text, lang):
    translation = translator.translate(text, dest='ta' if lang == 'Tamil' else lang)
    return translation.text


def recommender(lang):
    def call_translate(text):
        if lang == "Malay":
            return translate_to_malay(text, lang)
        elif lang == "Chinese":
            return translate_to_chinese(text, lang)
        elif lang == "Tamil":
            return translate_to_tamil(text, lang)
        else:
            return text

    def poster(movie_id):
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
            movie_id)
        data = requests.get(url)
        data = data.json()
        poster_path = data['poster_path']
        path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return path

    def recommend(movie):
        pointer = movies[movies['title'] == movie].index[0]
        distance = sorted(list(enumerate(similarity[pointer])), reverse=True, key=lambda x: x[1])
        recommended_movie_name = []
        recommended_movie_poster = []
        for i in distance[1:6]:
            # obtaining respective movie posters
            movie_id = movies.iloc[i[0]].id
            recommended_movie_poster.append(poster(movie_id))
            recommended_movie_name.append(movies.iloc[i[0]].title)

        return recommended_movie_name, recommended_movie_poster

    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        call_translate("Type or select a movie from the dropdown"),
        movie_list
    )

    if st.button(call_translate('Show Recommendation')):
        recommended_movie_name, recommended_movie_poster = recommend(selected_movie)
        num_columns = 5
        cols = st.columns(num_columns)

        for i in range(num_columns):
            with cols[i]:
                st.text(recommended_movie_name[i])
                st.image(recommended_movie_poster[i])


def main():
    # Add language selection dropdown menu
    lang = st.selectbox("Select Language", ("English", "Malay", "Chinese", "Tamil"))

    # Use selected language to translate text
    def call_translate(text):
        if lang == "Malay":
            return translate_to_malay(text, lang)
        elif lang == "Chinese":
            return translate_to_chinese(text, lang)
        elif lang == "Tamil":
            return translate_to_tamil(text, lang)
        else:
            return text

    # Display the title
    st.title(call_translate("Yurnero's Recommendations"))

    # Display the navigation menu
    menu = [call_translate("Home Page"), call_translate("Login Page"), call_translate("Sign Up Page")]
    choice = st.sidebar.selectbox(call_translate("Select an option"), menu)

    # Display the appropriate page based on the user's choice
    if choice == call_translate("Home Page"):
        st.write(call_translate("Welcome to Yurnero's Recommendations!"))
        st.write(call_translate("Nice to meet you fellow movie enjoyers!"))
        st.write(call_translate("We are here to help you clear your confusions on movie choices!"))
        st.image("movies-cell.webp", width=710, use_column_width=False)
    elif choice == call_translate("Login Page"):
        user_name = call_translate("Username")
        password_str = call_translate("Password")
        login_str = call_translate('Login')
        logged_in_as_str = call_translate('Logged in as {}')
        incorrect_credentials_str = call_translate('Incorrect username/password')

        username = st.sidebar.text_input(user_name, key="username", max_chars=20)
        password = st.sidebar.text_input(password_str, key="password", type="password", max_chars=20)

        if st.sidebar.checkbox(login_str):
            if not username or not password:
                st.warning(call_translate("Please enter a username and password."))
            else:
                if authenticate_user(username, password):
                    st.success(logged_in_as_str.format(username))
                    # Call recommender function here
                    recommender(lang)
                else:
                    st.error(incorrect_credentials_str)
    elif choice == call_translate("Sign Up Page"):
        st.subheader(call_translate("Create New Account"))
        new_username = st.text_input(call_translate("User Name"), key='new_username', max_chars=20)
        new_password = st.text_input(call_translate("Password"), type='password', key='new_password', max_chars=20)
        confirm_password = st.text_input(call_translate("Confirm Password"), type='password', key='confirm_password',
                                         max_chars=20)
        if st.button(call_translate("Create Account"), key='create_account'):
            if not new_username or not new_password or not confirm_password:
                st.warning(call_translate("Please fill in all the required fields."))
            elif new_password != confirm_password:
                st.warning(call_translate("Passwords do not match."))
            else:
                create_table()
                if add_user(new_username, new_password):
                    st.success(call_translate("Account created!"))
                else:
                    st.warning(call_translate("Account already exists."))


if __name__ == '__main__':
    main()
