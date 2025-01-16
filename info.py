import tkinter as tk
from tkinter import scrolledtext

class Info(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # Main frame for content
        info_frame = tk.Frame(self, bg="#1e1e1e")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title Label
        tk.Label(
            info_frame,
            text="Modix Game Panel - Game Server Manager",
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Courier New", 18, "bold")
        ).pack(pady=10)

        # Scrolled Text for License and Terms
        self.info_text = scrolledtext.ScrolledText(
            info_frame, wrap=tk.WORD, bg="#000000", fg="#00ff00",
            font=("Courier New", 12), height=20
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.insert(tk.END, (
            "License Information\n"
            "--------------------\n\n"
            "The Modix Game Panel is available for free for personal and non-commercial use. Hosting companies or those providing "
            "server hosting services will need an extended license, priced at £5 per month.\n\n"
            "Extended License\n"
            "------------------\n"
            "With the extended license, Modix Game Panel will be linked to your domain's URL or IP address, ensuring seamless integration with your "
            "hosting infrastructure.\n\n"
            "Please remember that selling Modix Game Panel as part of your hosting services without the extended license is not permitted. For more "
            "information or assistance with obtaining the extended license, please email us at support@modix-store.co.uk. Note that this process "
            "may change once our website is updated. Modix Game Panel is budget-friendly and designed to be accessible for everyone!\n\n"
            "Terms of Use\n"
            "----------------\n\n"
            "Welcome to Modix Game Panel ('we,' 'our,' or 'us'). These Terms of Use govern your access to and use of our gaming control panel services ('Services'). By using our Services, you agree to comply with and be bound by these terms and conditions. If you do not agree with these Terms of Use, please do not use our Services.\n\n"
            "1. Acceptance of Terms\n"
            "   - By accessing or using our Services, you agree to be bound by these Terms of Use. We may update these Terms from time to time, and your continued use of our Services constitutes acceptance of any changes.\n\n"
            "2. License and Use\n"
            "   - License Grant: Modix Game Panel grants you a non-exclusive, non-transferable license to use our Services in accordance with these Terms. This license is limited to managing and configuring game servers as intended by our software.\n"
            "   - Free and Extended License:\n"
            "     - Free License: The Modix Game Panel is available for free for personal and non-commercial use.\n"
            "     - Extended License: Hosting companies or those providing server hosting services will need an extended license, priced at £5 per month. With the extended license, Modix Game Panel will be linked to your domain's URL or IP address, ensuring seamless integration with your hosting infrastructure.\n"
            "   - Prohibited Uses: You may not:\n"
            "     - Use the Services for any illegal purposes or to facilitate illegal activities.\n"
            "     - Attempt to reverse-engineer, decompile, or disassemble the Services.\n"
            "     - Distribute, rent, lease, or sublicense the Services without Modix Game Panel's prior written consent.\n"
            "     - Sell Modix Game Panel as part of your hosting services without the extended license.\n\n"
            "3. Account Management\n"
            "   - While our Services do not involve traditional user accounts with usernames or passwords, you are responsible for securing any access credentials or configurations related to your use of the Services.\n\n"
            "4. Acceptable Use Policy\n"
            "   - You agree to use our Services in compliance with our Acceptable Use Policy, which prohibits:\n"
            "     - Engaging in spamming, phishing, or other malicious activities.\n"
            "     - Actions that harm or disrupt the performance or stability of the Services or other users' servers.\n"
            "     - Harassment or abuse of other users or their servers.\n\n"
            "5. Intellectual Property\n"
            "   - All software, content, and materials provided through our Services are owned by Modix Game Panel or its licensors. You may not copy, modify, distribute, or create derivative works from these materials without Modix Game Panel's express written permission.\n\n"
            "6. Service Availability\n"
            "   - We aim to provide reliable and uninterrupted Services, but cannot guarantee continuous availability. Maintenance or updates may affect Service availability.\n\n"
            "7. Fees and Payments\n"
            "   - Certain features or usage of our Services may incur fees as specified in your service plan. You agree to pay all applicable fees in accordance with your plan. Modix Game Panel may adjust fees and billing terms with prior notice.\n\n"
            "8. Termination\n"
            "   - Modix Game Panel reserves the right to suspend or terminate access to our Services at our discretion, with or without cause, and with or without notice. Upon termination, you must cease all use of our Services and delete any related data or configurations.\n\n"
            "9. Limitation of Liability\n"
            "   - To the fullest extent permitted by law, Modix Game Panel shall not be liable for any indirect, incidental, or consequential damages arising from your use of the Services. Our liability for direct damages is limited to the amount you have paid for the Services in question.\n\n"
            "10. Indemnification\n"
            "    - You agree to indemnify and hold harmless Modix Game Panel, its affiliates, and their respective officers, directors, and employees from any claims, liabilities, damages, losses, or expenses (including legal fees) arising out of your use of the Services or violation of these Terms.\n\n"
            "11. Governing Law\n"
            "    - These Terms of Use are governed by the laws of the United Kingdom. Any disputes arising under or in connection with these Terms will be resolved in the courts of the United Kingdom.\n\n"
            "12. Contact Information\n"
            "    - For questions regarding these Terms of Use or our Services, please contact us at:\n\n"
            "      Modix Game Panel\n"
            "      For licensing inquiries: support@modix-store.co.uk\n\n"
            "13. Miscellaneous\n"
            "    - Severability: If any provision of these Terms is deemed invalid or unenforceable, the remaining provisions will continue in full force.\n"
            "    - Waiver: A failure to enforce any provision of these Terms does not constitute a waiver of that provision.\n"
            "    - Assignment: Modix Game Panel may transfer its rights and obligations under these Terms to a third party. You may not assign your rights or obligations without Modix Game Panel's prior written consent.\n\n"
            "14. Licensing Note\n"
            "    - Modix Game Panel is budget-friendly and designed to be accessible for everyone. For more information or assistance with obtaining the extended license, please email us at support@modix-store.co.uk. Note that this process may change once our website is updated."
        ))

        # Optional: Add a footer or additional information if needed
        footer_frame = tk.Frame(info_frame, bg="#1e1e1e")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Label(
            footer_frame,
            text="Thank you for using Modix Game Panel!",
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Courier New", 10)
        ).pack(pady=5)
