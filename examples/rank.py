from easy_pil import Editor, Canvas, Font, canvas,font

background = Editor("../assets/bg.png")
profile = Editor("../assets/schtabtag.jpg").resize((150,150)).circle_image()
poppins = Font.poppins(size=40)
poppins_small = Font.poppins(size=20)

square = Canvas((500,500),"#AC27FA")
square = Editor(square)
square.rotate(30,expand=True)

background.paste(square.image,(600,-250))
background.paste(profile.image,(30,30))

background.rectangle((30,220),width=650,height=40,fill="white",radius=20)
background.bar((30,220),max_width=650,height=40,percentage=40,fill="#AC27FA",radius=20)
background.text((200,50),"Ahmed Amr#5544",font=poppins,color="white")

background.rectangle((200,100),width=350,height=2,fill="#AC27FA")
background.text((200,125),"Level : 113",font=poppins,color="white")
background.text((200,165),"XP : 10K / 20K",font=poppins,color="white")

background.save("card.png")
