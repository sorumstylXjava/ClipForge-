package com.clipforge.data.remote.api

import com.clipforge.domain.model.Video
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface VideoApi {
    @GET("videos")
    suspend fun getVideos(): VideoListResponse

    @POST("videos/import")
    suspend fun importVideo(@Body req: Map<String, String>): Video
}

data class VideoListResponse(val videos: List<Video>)
