import os

# Update index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

idx = idx.replace('The Art of Visual Storytelling', "{{ site_settings.get('hero_subtitle', 'The Art of Visual Storytelling') }}")
# Ensure we don't double replace
if 'site_settings.get(' not in idx:
    # already replaced? wait, above replace might fail if string doesn't exist but it does.
    pass

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update footer.html
with open('templates/includes/footer.html', 'r', encoding='utf-8') as f:
    foot = f.read()

foot = foot.replace('Colombo, Sri Lanka', "{{ site_settings.get('contact_address', 'Colombo, Sri Lanka') }}")
foot = foot.replace('pulindu@svems.com', "{{ site_settings.get('contact_email', 'pulindu@svems.com') }}")
foot = foot.replace('+94 77 123 4567', "{{ site_settings.get('contact_phone', '+94 77 123 4567') }}")
foot = foot.replace('href="#" aria-label="Instagram"', 'href="{{ site_settings.get(\'instagram_url\', \'#\') }}" aria-label="Instagram"')
foot = foot.replace('href="#" aria-label="Facebook"', 'href="{{ site_settings.get(\'facebook_url\', \'#\') }}" aria-label="Facebook"')

with open('templates/includes/footer.html', 'w', encoding='utf-8') as f:
    f.write(foot)

print("Updated templates")
