package com.clipforge.domain.model

data class Clip(
    val id: String,
    val videoId: String,
    val title: String,
    val clipType: String,
    val duration: Double,
    val hasWatermark: Boolean,
    val status: String
)
