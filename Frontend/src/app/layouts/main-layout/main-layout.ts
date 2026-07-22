import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '../../shared/components/sidebar/sidebar';
import { TopbarComponent } from '../../shared/components/topbar/topbar';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, TopbarComponent],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MainLayoutComponent {
  sidebarCollapsed = signal<boolean>(false);
  mobileSidebarOpen = signal<boolean>(false);

  toggleSidebar(): void {
    const isMobile = typeof window !== 'undefined' ? window.innerWidth <= 991 : false;
    if (isMobile) {
      this.mobileSidebarOpen.update((v) => !v);
    } else {
      this.sidebarCollapsed.update((v) => !v);
    }
  }

  closeMobileSidebar(): void {
    this.mobileSidebarOpen.set(false);
  }
}