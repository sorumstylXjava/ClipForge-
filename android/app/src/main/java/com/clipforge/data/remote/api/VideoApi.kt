package com.clipforge.data.remote.api

import com.clipforge.domain.model.Video
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

data class ImportVideoRequest(
    val youtube_url: String,
    val youtube_id: String,
    val title: String = "",
    val thumbnail_url: String = "",
    val duration_seconds: Int = 0
)

interface VideoApi {
    @GET("videos/")
    suspend fun getVideos(): List<Video>

    @POST("videos/import")
    suspend fun importVideo(@Body req: ImportVideoRequest): Video

    @DELETE("videos/{id}")
    suspend fun deleteVideo(@Path("id") id: String): Video
}
