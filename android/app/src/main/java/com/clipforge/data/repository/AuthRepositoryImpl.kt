package com.clipforge.data.repository

import com.clipforge.data.remote.api.AuthApi
import com.clipforge.data.remote.api.RegisterRequest
import com.clipforge.domain.model.User
import com.clipforge.domain.repository.AuthRepository
import com.clipforge.data.local.datastore.SessionManager
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi,
    private val sessionManager: SessionManager
) : AuthRepository {
    override fun login(email: String, pass: String): Flow<Result<User>> = flow {
        try {
            val tokenResponse = api.login(email, pass)
            val token = tokenResponse.access_token
            // Save token first
            sessionManager.saveSession(token, "", "")
            // Then fetch user details
            val user = api.getMe()
            sessionManager.saveSession(token, user.id, user.plan)
            emit(Result.success(user))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun register(email: String, pass: String, name: String): Flow<Result<User>> = flow {
        try {
            val request = RegisterRequest(email = email, password = pass, fullName = name)
            val user = api.register(request)
            emit(Result.success(user))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun getMe(): Flow<Result<User>> = flow {
        try {
            emit(Result.success(api.getMe()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun logout(): Flow<Result<Unit>> = flow {
        try {
            sessionManager.clearSession()
            emit(Result.success(Unit))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
