package com.clipforge.domain.model

data class User(
    val id: String,
    val email: String,
    val fullName: String,
    val plan: String,
    val isPremium: Boolean = plan == "premium"
)
