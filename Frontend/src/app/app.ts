import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Chatbot } from './shared/components/chatbot/chatbot';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Chatbot],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}

