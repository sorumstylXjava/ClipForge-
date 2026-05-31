package com.clipforge.domain.repository

import com.clipforge.domain.model.User
import kotlinx.coroutines.flow.Flow

interface AuthRepository {
    fun login(email: String, pass: String): Flow<Result<User>>
    fun register(email: String, pass: String, name: String): Flow<Result<User>>
    fun getMe(): Flow<Result<User>>
    fun logout(): Flow<Result<Unit>>
}
