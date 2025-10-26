# Svems Photography

**Svems Photography** is a professional photography portfolio website built with **Flask**, **HTML**, **CSS**, and **JavaScript**. This website showcases the photography services of Pulindu Peiris, specializing in portrait, landscape, event, and commercial photography. Users can view a gallery of images, contact the photographer, and book sessions online.

## Features

- **Portfolio Gallery**: Display images from different categories like portraits, landscapes, events, etc.
- **Admin Panel**: Manage gallery images, view contact messages, and manage other settings.
- **Responsive Design**: The site is optimized for desktop, tablet, and mobile devices.
- **Upload Images**: Admin can upload new images to the gallery.
- **Flash Messages**: Notifications for the admin panel (e.g., success or error messages).
- **File Upload**: Drag and drop or click to upload images with preview support.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB (for storing images, messages, and other data)
- **Styling**: Custom CSS with Flexbox, Grid Layout, and responsive design techniques
- **Icons**: Font Awesome

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/username/svems-photography.git
    cd svems-photography
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    - **Windows**: 
      ```bash
      venv\Scripts\activate
      ```
    - **Mac/Linux**:
      ```bash
      source venv/bin/activate
      ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Set up MongoDB and add the necessary configurations in your `.env` file.

6. Run the Flask application:

    ```bash
    flask run
    ```

   The app should now be accessible at `http://127.0.0.1:5000/`.

## Admin Panel

To log in to the admin panel, visit the login page and enter the credentials. The admin can:
- View and manage the gallery images.
- View messages from the contact form.
- Perform other admin functions (like marking messages as read).

## File Structure

- `static/`: Contains static assets like images, CSS, and JavaScript files.
- `templates/`: Contains HTML templates for the website.
- `app.py`: Main Flask application file.
- `config.py`: Configuration for Flask app, including database settings.
- `requirements.txt`: List of dependencies.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For inquiries, please contact:

- **Pulindu Peiris** – [pulindu@svems.com](mailto:pulindu@svems.com)

Feel free to check out the site and explore the work!

