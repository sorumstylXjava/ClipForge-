package com.clipforge.presentation.screen.importvideo

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.clipforge.domain.model.Video
import com.clipforge.domain.repository.VideoRepository
import com.clipforge.presentation.state.UIState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class VideoViewModel @Inject constructor(
    private val videoRepository: VideoRepository
) : ViewModel() {

    private val _videosState = MutableStateFlow<UIState<List<Video>>>(UIState.Idle)
    val videosState: StateFlow<UIState<List<Video>>> = _videosState

    private val _importState = MutableStateFlow<UIState<Video>>(UIState.Idle)
    val importState: StateFlow<UIState<Video>> = _importState

    init {
        loadVideos()
    }

    fun loadVideos() {
        _videosState.value = UIState.Loading
        viewModelScope.launch {
            videoRepository.getVideos().collect {
                _videosState.value = if (it.isSuccess)
                    UIState.Success(it.getOrThrow())
                else
                    UIState.Error(it.exceptionOrNull()?.message ?: "Failed to load videos")
            }
        }
    }

    fun importVideo(url: String) {
        if (url.isBlank()) return
        _importState.value = UIState.Loading
        viewModelScope.launch {
            videoRepository.importVideo(url).collect {
                _importState.value = if (it.isSuccess) {
                    loadVideos()
                    UIState.Success(it.getOrThrow())
                } else {
                    UIState.Error(it.exceptionOrNull()?.message ?: "Failed to import video")
                }
            }
        }
    }

    fun deleteVideo(id: String) {
        viewModelScope.launch {
            videoRepository.deleteVideo(id).collect {
                if (it.isSuccess) loadVideos()
            }
        }
    }

    fun resetImportState() {
        _importState.value = UIState.Idle
    }
}
