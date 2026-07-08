import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface ChatMessage {
  from: 'user' | 'bot';
  text: string;
}

interface AskResponse {
  question: string;
  answer: string;
  sources: {
    source: string;
    page: number;
    content_preview: string;
  }[];
  processing_time_seconds: number;
}

@Injectable({ providedIn: 'root' })
export class ChatbotService {
  private apiUrl = 'http://127.0.0.1:8100/ask';

  constructor(private http: HttpClient) {}

  sendMessage(question: string): Observable<string> {
    return this.http.post<AskResponse>(this.apiUrl, { question }).pipe(
      map(res => res.answer)
    );
  }
}