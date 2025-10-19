# Language Support Quick Reference

## Available Languages

| Language | Code | Native Name |
|----------|------|-------------|
| English | en | English |
| Estonian | et | Eesti |
| Hungarian | hu | Magyar |
| Lithuanian | lt | Lietuvių |
| Polish | pl | Polski |
| Portuguese | pt | Português |
| Slovak | sk | Slovenčina |
| Slovenian | sl | Slovenščina |

## How to Switch Languages

### User Interface Method
1. Look for the **Language** button in the top navigation bar
2. Click the dropdown arrow next to "Language"
3. Select your preferred language from the list
4. The page will automatically reload with the new language

### API Method (for developers)
```bash
curl -X POST http://localhost:5000/api/set-language/et
```

Replace `et` with any supported language code.

## Language Files Location
All translation files are located in:
```
prototype3/translations/
├── en/LC_MESSAGES/messages.mo
├── et/LC_MESSAGES/messages.mo
├── hu/LC_MESSAGES/messages.mo
├── lt/LC_MESSAGES/messages.mo
├── pl/LC_MESSAGES/messages.mo
├── pt/LC_MESSAGES/messages.mo
├── sk/LC_MESSAGES/messages.mo
└── sl/LC_MESSAGES/messages.mo
```

## Current Implementation

### Translation Sources
- **Navigation**: Home, Start Assessment, Dashboard, About, Language
- **Common UI Elements**: Page titles, buttons, labels
- **Error Pages**: 404 and 500 error messages
- **Home Page**: Statistics labels and calls-to-action

### Technology Stack
- **Framework**: Flask-Babel
- **Format**: GNU Gettext (.po/.mo files)
- **Storage**: Session-based (per user)
- **Detection**: Browser Accept-Language header + user preference

## Notes
- Language preference is stored in the user's Flask session
- The default language is English
- All original app functionality remains unchanged
- Session persists across page navigation
