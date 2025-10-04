
import argostranslate.package
import argostranslate.translate

def setup_argos():
    """Downloads and installs Argos Translate language packages if not present."""
    try:
        print("Updating package index...")
        argostranslate.package.update_package_index()
        print("Getting available packages...")
        available_packages = argostranslate.package.get_available_packages()
        print("Available packages:", available_packages)
        
        print("Finding English package...")
        package_to_install = next(
            filter(
                lambda x: x.from_code == "en" and x.to_code == "en",
                available_packages,
            )
        )
        if not package_to_install.is_installed():
            print("Downloading and installing Argos Translate English package...")
            package_to_install.install()
            print("Installation complete.")
        else:
            print("English package already installed.")
            
        print("Verifying installation...")
        installed_langs = argostranslate.translate.get_installed_languages()
        en_lang = next(filter(lambda x: x.code == 'en', installed_langs))
        translator = en_lang.get_translation(en_lang)
        if translator:
            print("Successfully initialized EN->EN translator.")
        else:
            print("Failed to initialize EN->EN translator after installation.")

    except Exception as e:
        print(f"An error occurred during Argos Translate setup: {repr(e)}")

if __name__ == "__main__":
    setup_argos()
