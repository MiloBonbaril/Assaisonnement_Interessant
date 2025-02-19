import polib

po = polib.pofile('locale/fr/LC_MESSAGES/prompts.po', encoding='utf-8')
po.save_as_mofile('locale/fr/LC_MESSAGES/prompts.mo')
