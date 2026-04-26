import { Injectable, signal } from '@angular/core';

const STORAGE_KEY = 'aci_taller_id';

@Injectable({ providedIn: 'root' })
export class TallerContextService {
  private readonly tallerIdSignal = signal<string | null>(localStorage.getItem(STORAGE_KEY));

  readonly tallerId = this.tallerIdSignal.asReadonly();

  setTallerId(tallerId: string): void {
    const value = tallerId.trim();
    if (!value) {
      this.clearTallerId();
      return;
    }
    localStorage.setItem(STORAGE_KEY, value);
    this.tallerIdSignal.set(value);
  }

  clearTallerId(): void {
    localStorage.removeItem(STORAGE_KEY);
    this.tallerIdSignal.set(null);
  }
}
