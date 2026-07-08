package edu.utleon.idgs902.app_movil_android.Controllers

import edu.utleon.idgs902.app_movil_android.Utils.LoginRequest
import edu.utleon.idgs902.app_movil_android.Utils.LoginResponse
import edu.utleon.idgs902.app_movil_android.Utils.VisionGuardApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity {

    private val api = VisionGuardApiService.create()

    fun login(
        correo: String,
        contrasena: String,
        onSuccess: (LoginResponse) -> Unit,
        onError: (String) -> Unit
    ) {
        api.login(LoginRequest(correo, contrasena))
            .enqueue(object : Callback<LoginResponse> {
                override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                    val body = response.body()
                    if (response.isSuccessful && body != null) {
                        onSuccess(body)
                    } else {
                        val mensaje = when (response.code()) {
                            401 -> "Correo o contraseña inválidos"
                            403 -> "El usuario está inactivo"
                            else -> "Error inesperado (${response.code()})"
                        }
                        onError(mensaje)
                    }
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    onError("Error de conexión: ${t.message}")
                }
            })
    }
}