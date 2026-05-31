package com.clipforge.data.repository

import com.clipforge.data.remote.api.VideoApi
import com.clipforge.domain.model.Video
import com.clipforge.domain.repository.VideoRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class VideoRepositoryImpl @Inject constructor(
    private val api: VideoApi
) : VideoRepository {
    override fun getVideos(): Flow<Result<List<Video>>> = flow {
        try {
            val response = api.getVideos()
            emit(Result.success(response.videos))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
