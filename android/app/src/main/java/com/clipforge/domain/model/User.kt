package com.clipforge.domain.model

import com.google.gson.annotations.SerializedName

data class User(
    val id: String = "",
    val email: String = "",
    @SerializedName("full_name")
    val fullName: String = "",
    val plan: String = "free"
) {
    val isPremium: Boolean get() = plan == "premium"
}
