package com.clipforge.data.remote.api

import retrofit2.http.GET
import retrofit2.http.POST

interface SubscriptionApi {
    @GET("subscriptions/me")
    suspend fun getSubscription(): Any
}
