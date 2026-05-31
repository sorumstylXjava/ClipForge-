package com.clipforge.domain.repository

import com.clipforge.domain.model.Clip
import kotlinx.coroutines.flow.Flow

interface ClipRepository {
    fun getClips(): Flow<Result<List<Clip>>>
}
