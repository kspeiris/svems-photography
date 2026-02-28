import os

file_path = "templates/admin/base_admin.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

nav_item = """                <li><a href="{{ url_for('admin_settings') }}" class="{% if request.endpoint == 'admin_settings' %}active{% endif %}">
                    <i class="fas fa-cog"></i> Settings
                </a></li>
"""

target = '<li><a href="{{ url_for(\'admin_messages\')" class="{% if request.endpoint == \'admin_messages\' %}active{% endif %}">\n                    <i class="fas fa-envelope"></i> Messages\n                </a></li>'

if 'admin_settings' not in content:
    # Just insert it before the View Site link instead since it's easier to find
    content = content.replace('<li><a href="{{ url_for(\'home\')" target="_blank">', nav_item + '                <li><a href="{{ url_for(\'home\')" target="_blank">')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done base_admin.html")
