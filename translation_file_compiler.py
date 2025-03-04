def compile_translation_files():
    import polib

    languages = ['en', 'fr']

    for lang in languages:
        po = polib.pofile(f'locale/{lang}/LC_MESSAGES/prompts.po', encoding='utf-8')
        po.save_as_mofile(f'locale/{lang}/LC_MESSAGES/prompts.mo')


if __name__ == "__main__":
    compile_translation_files()