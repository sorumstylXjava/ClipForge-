package com.clipforge.domain.repository

import com.clipforge.domain.model.Video
import kotlinx.coroutines.flow.Flow

interface VideoRepository {
    fun getVideos(): Flow<Result<List<Video>>>
    fun importVideo(youtubeUrl: String): Flow<Result<Video>>
    fun deleteVideo(id: String): Flow<Result<Video>>
}
