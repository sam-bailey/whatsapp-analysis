from whatsanalysis.whatsapp_chat import WhatsAppChat
import matplotlib.pyplot as plt

file_name = '../whatsapp-conversations/Fingers_chat.convo'
test_chat = WhatsAppChat(file_name)

test_chat.find_people()
test_chat.plot_messages_over_time(person=['Feebs'], bins=50, alpha=0.5)
plt.show()