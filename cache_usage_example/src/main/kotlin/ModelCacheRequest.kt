import com.google.gson.annotations.SerializedName

data class ModelCacheRequest(
    val type: Type,
    val scope: Scope = Scope(Model.CODEGPT_1008),
    @SerializedName("chat_info")
    val chatInfo: List<Query>? = null,
    val query: List<QueryEntry>? = null,
    @SerializedName("remove_type")
    val removeType: RemoveType? = null,
) {
    enum class Type {
        @SerializedName("insert")  INSERT,
        @SerializedName("query")   QUERY,
        @SerializedName("remove")  REMOVE
    }

    enum class Model {
        @SerializedName("CODEGPT-1008")  CODEGPT_1008;
    }

    enum class RemoveType {
        @SerializedName("truncate_by_model")  TRUNCATE_BY_MODEL,
    }

    enum class Role {
        @SerializedName("user")    USER,
        @SerializedName("system")  SYSTEM,
    }

    data class Scope(val model: Model)

    data class QueryEntry(
        val role: Role,
        val content: String,
    )

    data class Query(
        val query: List<QueryEntry>,
        val answer: String,
    )
}