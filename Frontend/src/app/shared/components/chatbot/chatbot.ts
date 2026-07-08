import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService, ChatMessage } from './chatbot.service';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.html',
  styleUrl: './chatbot.scss'
})
export class Chatbot {
  isOpen = signal(false);
  userInput = signal('');
  messages = signal<ChatMessage[]>([
    { from: 'bot', text: '¡Hola! ¿En qué puedo ayudarte?' }
  ]);
  loading = signal(false);

  constructor(private chatbotService: ChatbotService) {}

  toggleChat() {
    this.isOpen.update(v => !v);
  }

  sendMessage() {
    const text = this.userInput().trim();
    if (!text || this.loading()) return;

    this.messages.update(msgs => [...msgs, { from: 'user', text }]);
    this.userInput.set('');
    this.loading.set(true);

    this.chatbotService.sendMessage(text).subscribe({
      next: (answer) => {
        this.messages.update(msgs => [...msgs, { from: 'bot', text: answer }]);
        this.loading.set(false);
      },
      error: () => {
        this.messages.update(msgs => [...msgs, { from: 'bot', text: 'Ocurrió un error, intenta de nuevo.' }]);
        this.loading.set(false);
      }
    });
  }
}