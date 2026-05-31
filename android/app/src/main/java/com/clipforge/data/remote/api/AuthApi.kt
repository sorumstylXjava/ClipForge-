package com.clipforge.data.remote.api

import com.clipforge.domain.model.User
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.FormUrlEncoded
import retrofit2.http.Field

data class TokenResponse(val access_token: String, val token_type: String)

data class RegisterRequest(
    val email: String,
    val password: String,
    val full_name: String
)

data class GoogleAuthRequest(
    val id_token: String
)

interface AuthApi {
    @FormUrlEncoded
    @POST("login/access-token")
    suspend fun login(
        @Field("username") email: String,
        @Field("password") pass: String
    ): TokenResponse

    @POST("users/")
    suspend fun register(@Body req: RegisterRequest): User

    @POST("auth/google")
    suspend fun loginWithGoogle(@Body req: GoogleAuthRequest): TokenResponse

    @GET("users/me")
    suspend fun getMe(): User
}
