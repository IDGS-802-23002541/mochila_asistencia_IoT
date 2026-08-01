import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})

export class Login {

  private fb = inject(FormBuilder);
  private router = inject(Router);

  loading = false;
  errorMessage = '';
  showPassword = false;

  loginForm = this.fb.group({
    username: ['', [Validators.required]],
    password: ['', [Validators.required, Validators.minLength(4)]]
  });

  get username() {
    return this.loginForm.get('username');
  }

  get password() {
    return this.loginForm.get('password');
  }

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.loading = true;

    // TODO: replace with real auth call to the ASP.NET Core API
    // this.authService.login(this.loginForm.value).subscribe({
    //   next: () => this.router.navigate(['/dispositivos']),
    //   error: (err) => { this.errorMessage = 'Usuario o contraseña incorrectos'; this.loading = false; }
    // });

    setTimeout(() => {
      this.loading = false;
      this.router.navigate(['/dispositivos']);
    }, 800);
  }
}