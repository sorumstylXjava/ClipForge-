import os

files = {
    # ViewModels
    "app/src/main/java/com/clipforge/presentation/screen/home/HomeViewModel.kt": """package com.clipforge.presentation.screen.home

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor() : ViewModel() {
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/importvideo/ImportVideoViewModel.kt": """package com.clipforge.presentation.screen.importvideo

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class ImportVideoViewModel @Inject constructor() : ViewModel() {
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/clips/ClipsViewModel.kt": """package com.clipforge.presentation.screen.clips

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class ClipsViewModel @Inject constructor() : ViewModel() {
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/projects/ProjectsViewModel.kt": """package com.clipforge.presentation.screen.projects

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class ProjectsViewModel @Inject constructor() : ViewModel() {
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/settings/SettingsViewModel.kt": """package com.clipforge.presentation.screen.settings

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor() : ViewModel() {
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/subscription/SubscriptionViewModel.kt": """package com.clipforge.presentation.screen.subscription

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class SubscriptionViewModel @Inject constructor() : ViewModel() {
}
""",

    # Retrofit Interfaces
    "app/src/main/java/com/clipforge/data/remote/api/ClipApi.kt": """package com.clipforge.data.remote.api

import com.clipforge.domain.model.Clip
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

interface ClipApi {
    @GET("clips")
    suspend fun getClips(): List<Clip>
}
""",
    "app/src/main/java/com/clipforge/data/remote/api/JobApi.kt": """package com.clipforge.data.remote.api

import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

interface JobApi {
    @GET("jobs")
    suspend fun getJobs(): List<Any>
}
""",
    "app/src/main/java/com/clipforge/data/remote/api/SubscriptionApi.kt": """package com.clipforge.data.remote.api

import retrofit2.http.GET
import retrofit2.http.POST

interface SubscriptionApi {
    @GET("subscriptions/me")
    suspend fun getSubscription(): Any
}
""",

    # Repositories
    "app/src/main/java/com/clipforge/domain/repository/VideoRepository.kt": """package com.clipforge.domain.repository

import com.clipforge.domain.model.Video
import kotlinx.coroutines.flow.Flow

interface VideoRepository {
    fun getVideos(): Flow<Result<List<Video>>>
}
""",
    "app/src/main/java/com/clipforge/data/repository/VideoRepositoryImpl.kt": """package com.clipforge.data.repository

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
""",
    "app/src/main/java/com/clipforge/domain/repository/ClipRepository.kt": """package com.clipforge.domain.repository

import com.clipforge.domain.model.Clip
import kotlinx.coroutines.flow.Flow

interface ClipRepository {
    fun getClips(): Flow<Result<List<Clip>>>
}
""",
    "app/src/main/java/com/clipforge/data/repository/ClipRepositoryImpl.kt": """package com.clipforge.data.repository

import com.clipforge.data.remote.api.ClipApi
import com.clipforge.domain.model.Clip
import com.clipforge.domain.repository.ClipRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class ClipRepositoryImpl @Inject constructor(
    private val api: ClipApi
) : ClipRepository {
    override fun getClips(): Flow<Result<List<Clip>>> = flow {
        try {
            emit(Result.success(api.getClips()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
""",
    "app/src/main/java/com/clipforge/domain/repository/SubscriptionRepository.kt": """package com.clipforge.domain.repository

import kotlinx.coroutines.flow.Flow

interface SubscriptionRepository {
    fun getSubscription(): Flow<Result<Any>>
}
""",
    "app/src/main/java/com/clipforge/data/repository/SubscriptionRepositoryImpl.kt": """package com.clipforge.data.repository

import com.clipforge.data.remote.api.SubscriptionApi
import com.clipforge.domain.repository.SubscriptionRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class SubscriptionRepositoryImpl @Inject constructor(
    private val api: SubscriptionApi
) : SubscriptionRepository {
    override fun getSubscription(): Flow<Result<Any>> = flow {
        try {
            emit(Result.success(api.getSubscription()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
"""
}

# Ensure directory structure exists and write files
for path, content in files.items():
    full_path = os.path.join("/sdcard/ClipForge/android", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Android fixes generated successfully.")
