import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth';

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
  private authService = inject(AuthService);

  loading = false;
  errorMessage = '';
  showPassword = false;


  loginForm = this.fb.group({
    correo: ['', [
      Validators.required,
      Validators.email
    ]],

    password: ['', [
      Validators.required,
      Validators.minLength(4)
    ]]
  });


  get correo() {
    return this.loginForm.get('correo');
  }


  get password() {
    return this.loginForm.get('password');
  }


  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }


  onSubmit(): void {

    this.errorMessage = '';

    if(this.loginForm.invalid){
      this.loginForm.markAllAsTouched();
      return;
    }


    this.loading = true;


    const correo = this.loginForm.value.correo ?? '';
    const contrasena = this.loginForm.value.password ?? '';


    this.authService.login(
      correo,
      contrasena
    )
    .subscribe({

      next:(respuesta)=>{


        console.log(
          'Usuario autenticado:',
          respuesta
        );


        localStorage.setItem(
          'usuario',
          JSON.stringify(respuesta)
        );


        this.loading = false;


        this.router.navigate([
          '/inicio'
        ]);


      },


      error:(error)=>{


        console.error(
          'Error login:',
          error
        );


        this.loading = false;


        this.errorMessage =
          error.error?.error ??
          'Correo o contraseña incorrectos';


      }


    });


  }

}