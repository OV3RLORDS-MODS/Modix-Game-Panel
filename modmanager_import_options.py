import zipfile
import requests
from io import BytesIO
from tkinter import simpledialog, messagebox
import os

class ImportSettings:
    def __init__(self, mod_directory):
        self.mod_directory = mod_directory

    def import_from_google_drive(self):
        """Import a mod from Google Drive."""
        google_drive_url = simpledialog.askstring("Google Drive URL", "Enter the Google Drive file URL:")
        if google_drive_url:
            try:
                file_id = google_drive_url.split('/')[-2]  # Extract file ID
                download_url = f"https://drive.google.com/uc?id={file_id}"
                response = requests.get(download_url)
                response.raise_for_status()
                with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                messagebox.showinfo("Success", "Mod imported from Google Drive successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def import_from_dropbox(self):
        """Import a mod from Dropbox."""
        dropbox_url = simpledialog.askstring("Dropbox URL", "Enter the Dropbox file URL:")
        if dropbox_url:
            try:
                download_url = dropbox_url.replace("?dl=0", "?dl=1")  # Adjust URL for direct download
                response = requests.get(download_url)
                response.raise_for_status()
                with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                messagebox.showinfo("Success", "Mod imported from Dropbox successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def import_from_github(self):
        """Import a mod from GitHub."""
        github_url = simpledialog.askstring("GitHub URL", "Enter the GitHub URL of the mod (ZIP file):")
        if github_url:
            try:
                response = requests.get(github_url)
                response.raise_for_status()
                with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                messagebox.showinfo("Success", "Mod imported from GitHub successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def import_from_steam(self):
        """Import a mod from Steam Workshop."""
        steam_mod_id = simpledialog.askstring("Steam Mod ID", "Enter the Steam Workshop Mod ID or URL:")
        if steam_mod_id:
            try:
                # Extract mod ID from URL if necessary
                if 'workshop' in steam_mod_id:
                    steam_mod_id = steam_mod_id.split('/')[-1]
                
                # Construct the Steam API URL to fetch the mod's file
                # Note: Steam does not provide direct download URLs for mods without authentication
                # You need to authenticate with Steam's API or use a library that can handle this
                # For demonstration purposes, we'll assume a direct URL construction method
                download_url = f"https://steamworkshopdownloader.io/download/{steam_mod_id}"
                
                response = requests.get(download_url)
                response.raise_for_status()
                
                with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(self.mod_directory)
                messagebox.showinfo("Success", "Mod imported from Steam successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")