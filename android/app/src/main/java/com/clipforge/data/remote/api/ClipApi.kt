package com.clipforge.data.remote.api

import com.clipforge.domain.model.Clip
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

interface ClipApi {
    @GET("clips")
    suspend fun getClips(): List<Clip>
}
