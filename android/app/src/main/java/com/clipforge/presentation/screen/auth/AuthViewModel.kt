package com.clipforge.presentation.screen.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.clipforge.domain.model.User
import com.clipforge.domain.repository.AuthRepository
import com.clipforge.presentation.state.UIState
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
                if (result.isSuccess) {
                    _loginState.value = UIState.Success(Unit)
                } else {
                    _loginState.value = UIState.Error(result.exceptionOrNull()?.message ?: "Login Failed")
                }
            }
        }
    }

    fun register(email: String, pass: String, name: String) {
        _registerState.value = UIState.Loading
        viewModelScope.launch {
            authRepository.register(email, pass, name).collect { result ->
                if (result.isSuccess) {
                    _registerState.value = UIState.Success(result.getOrThrow())
                } else {
                    _registerState.value = UIState.Error(result.exceptionOrNull()?.message ?: "Register Failed")
                }
            }
        }
    }
}
