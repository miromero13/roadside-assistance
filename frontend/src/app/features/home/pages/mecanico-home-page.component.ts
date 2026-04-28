import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-mecanico-home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './mecanico-home-page.component.html',
})
export class MecanicoHomePageComponent {}
