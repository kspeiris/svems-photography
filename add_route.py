import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

route_str = """
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        validate_csrf()
        settings_data = {
            'site_title': request.form.get('site_title') or 'Svems',
            'hero_subtitle': request.form.get('hero_subtitle') or 'The Art of Visual Storytelling',
            'contact_email': request.form.get('contact_email') or 'pulindu@svems.com',
            'contact_phone': request.form.get('contact_phone') or '+94 77 123 4567',
            'contact_address': request.form.get('contact_address') or 'Colombo, Sri Lanka',
            'instagram_url': request.form.get('instagram_url') or '',
            'facebook_url': request.form.get('facebook_url') or ''
        }
        try:
            mongo.db.settings.update_one({}, {'$set': settings_data}, upsert=True)
            flash('Settings updated successfully', 'success')
        except Exception:
            flash('Error updating settings', 'error')
        return redirect(url_for('admin_settings'))
    try:
        settings = mongo.db.settings.find_one({}) or {}
    except Exception:
        settings = {}
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/messages')
"""

if "@app.route('/admin/settings" not in content:
    content = content.replace("@app.route('/admin/messages')", route_str)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Done")
