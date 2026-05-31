package com.clipforge.data.repository

import com.clipforge.data.remote.api.ImportVideoRequest
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
            emit(Result.success(api.getVideos()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun importVideo(youtubeUrl: String): Flow<Result<Video>> = flow {
        try {
            val youtubeId = extractYoutubeId(youtubeUrl) ?: throw Exception("Invalid YouTube URL")
            val req = ImportVideoRequest(
                youtube_url = youtubeUrl,
                youtube_id = youtubeId
            )
            emit(Result.success(api.importVideo(req)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    override fun deleteVideo(id: String): Flow<Result<Video>> = flow {
        try {
            emit(Result.success(api.deleteVideo(id)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    private fun extractYoutubeId(url: String): String? {
        val patterns = listOf(
            Regex("(?:youtube\\.com/watch\\?v=|youtu\\.be/)([\\w-]{11})"),
            Regex("youtube\\.com/shorts/([\\w-]{11})")
        )
        for (pattern in patterns) {
            val match = pattern.find(url)
            if (match != null) return match.groupValues[1]
        }
        return null
    }
}
