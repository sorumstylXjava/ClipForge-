package com.clipforge.presentation.screen.auth

import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.GetCredentialRequest
import androidx.credentials.exceptions.GetCredentialException
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.clipforge.domain.model.User
import com.clipforge.domain.repository.AuthRepository
import com.clipforge.presentation.state.UIState
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<UIState<Unit>>(UIState.Idle)
    val loginState: StateFlow<UIState<Unit>> = _loginState

    private val _registerState = MutableStateFlow<UIState<User>>(UIState.Idle)
    val registerState: StateFlow<UIState<User>> = _registerState

    fun login(email: String, pass: String) {
        _loginState.value = UIState.Loading
        viewModelScope.launch {
            authRepository.login(email, pass).collect { result ->
                _loginState.value = if (result.isSuccess) {
                    UIState.Success(Unit)
                } else {
                    UIState.Error(result.exceptionOrNull()?.message ?: "Login Failed")
                }
            }
        }
    }

    fun register(email: String, pass: String, name: String) {
        _registerState.value = UIState.Loading
        viewModelScope.launch {
            authRepository.register(email, pass, name).collect { result ->
                _registerState.value = if (result.isSuccess) {
                    UIState.Success(result.getOrThrow())
                } else {
                    UIState.Error(result.exceptionOrNull()?.message ?: "Register Failed")
                }
            }
        }
    }

    fun loginWithGoogle(context: Context, webClientId: String) {
        _loginState.value = UIState.Loading
        viewModelScope.launch {
            try {
                val credentialManager = CredentialManager.create(context)
                val googleIdOption = GetGoogleIdOption.Builder()
                    .setFilterByAuthorizedAccounts(false)
                    .setServerClientId(webClientId)
                    .build()
                val request = GetCredentialRequest.Builder()
                    .addCredentialOption(googleIdOption)
                    .build()
                val result = credentialManager.getCredential(context, request)
                val googleIdToken = GoogleIdTokenCredential
                    .createFrom(result.credential.data)
                    .idToken

                authRepository.loginWithGoogle(googleIdToken).collect { res ->
                    _loginState.value = if (res.isSuccess) {
                        UIState.Success(Unit)
                    } else {
                        UIState.Error(res.exceptionOrNull()?.message ?: "Google Login Failed")
                    }
                }
            } catch (e: GetCredentialException) {
                _loginState.value = UIState.Error(e.message ?: "Google Login Failed")
            } catch (e: Exception) {
                _loginState.value = UIState.Error(e.message ?: "Google Login Failed")
            }
        }
    }
}
