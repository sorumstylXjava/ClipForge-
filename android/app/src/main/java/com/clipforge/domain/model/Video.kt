package com.clipforge.domain.model

data class Video(
    val id: String,
    val youtubeId: String,
    val title: String,
    val thumbnailUrl: String,
    val durationSeconds: Int,
    val status: String
)
