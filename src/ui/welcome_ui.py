# TODO: Make welcome card

# import discord
# from PIL import Image, ImageDraw, ImageFont


# class WelcomeCard(discord.ui.View):
#     def __init__(self, interaction: discord.Interaction):
#         super().__init__()
#         self.interaction = interaction
#         self.profile_picture = load_image(str(interaction.user.avatar))

#         self.background = Editor(Canvas((900, 270), color="#23272a"))
#         self.profile = Editor(self.profile_picture).resize((200, 200)).circle_image()

#         # fonts
#         poppins_big = Font.poppins(variant="bold", size=50)
#         poppins_medium = Font.poppins(variant="bold", size=40)
#         poppins_regular = Font.poppins(variant="regular", size=30)

#         card_left_shape = [(0, 0), (0, 270), (330, 270), (260, 0)]

#         self.background.polygon(card_left_shape, "#2C2F33")
#         self.background.paste(self.profile, (40, 35))
#         self.background.ellipse((40, 35), 200, 200, outline="white", stroke_width=3)
#         self.background.text((600, 20), "WELCOME", font=poppins_big, color="white", align="center")
#         self.background.text(
#             (600, 70),
#             self.interaction.user.display_name,
#             font=poppins_regular,
#             color="white",
#             align="center",
#         )
#         self.background.text(
#             (600, 120),
#             "TO ETHEREAL HYPERSPACE BATTLESHIPS!",
#             font=poppins_medium,
#             color="white",
#             align="center",
#         )
