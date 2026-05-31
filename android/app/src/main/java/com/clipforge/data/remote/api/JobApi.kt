package com.clipforge.data.remote.api

import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

interface JobApi {
    @GET("jobs")
    suspend fun getJobs(): List<Any>
}
