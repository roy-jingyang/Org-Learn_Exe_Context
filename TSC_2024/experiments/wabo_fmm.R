# Built on the original R implementation code available at:
# https://doi.org/10.5281/zenodo.4606757
# Reference:
# van Hulzen, G., Martin, N., & Depaire, B. (2021). Looking Beyond Activity
# Labels: Mining Context-Aware Resource Profiles Using Activity Instance
# Archetypes. In A. Polyvyanyy, M. T. Wynn, A. Van Looy, & M. Reichert (Eds.),
# Business Process Management Forum - BPM Forum 2021, Rome, Italy, September
# 06-10, 2021, Proceedings (pp. 230–245). Springer.

require(dplyr)
require(lubridate)
require(stringr)
require(fastDummies)
require(flexmix)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 2) {
    fn <- args[1]
    k <- as.integer(args[2])
} else {
    stop("Need to specify two arguments `fn` (filename) and `k` (number of components)")
}

print(fn)
print(k)

# Read event log
wabo <- read.csv(
    file = fn,
    header = TRUE, 
    encoding = "UTF-8", 
    fileEncoding = "UTF-8-BOM", 
    stringsAsFactors = TRUE
)

# Preprocess data
# load and transform columns
wabo <- wabo %>%
    select(
        "case.channel",
        "case.department",
        "case.concept.name",
        "concept.name",
        "org.resource",
        "time.timestamp"
    ) %>%
    rename(
        CaseID = "case.concept.name",
        CaseChannel = "case.channel",
        CaseDepartment = "case.department",
        Activity = "concept.name",
        CompleteTimestamp = "time.timestamp",
        Resource = "org.resource"
    ) %>%
    mutate(
        CaseID = as.factor(CaseID),
        CaseChannel = as.factor(CaseChannel),
        CaseDepartment = as.factor(CaseDepartment),
        CompleteTimestamp = ymd_hms(CompleteTimestamp),
        Resource = as.factor(Resource),
        Activity = as.factor(Activity),
        Month = as.factor(month(CompleteTimestamp, label = FALSE)),
        Weekday = as.factor(wday(CompleteTimestamp, label = FALSE, week_start = 1))
    )
wabo <- as.data.frame(wabo)

# Run clustering with manual loop to store all models
modelBIC <- list()
niter <- 20
for (i in 1:niter) {
    cat(paste0("=== Iter ", i, " ===\n"))
    model <- tryCatch({stepFlexmix(
        formula = . ~ 1,
        data = wabo,
        k = k,
        nrep = 5,
        model = list(
            FLXMRmultinom(Resource ~ .),

            FLXMRmultinom(CaseChannel ~ .),
            FLXMRmultinom(CaseDepartment ~ .),

            FLXMRmultinom(Activity ~ .),

            FLXMRmultinom(Month ~ .),
            FLXMRmultinom(Weekday ~ .)
        ),
        control = list(
            verbose = 1,
            tolerance = 1e-06,
            iter.max = 500
        )
    )}, error = function(e) {
        return(NULL)
    })
    if (!is.null(model) && !any(is.na(logLik(model)))) {
        newCol <- paste0("ClusterRep", "_", i)
        wabo[[newCol]] <- clusters(model)
        val <- paste0("BICRep", "_", i)
        modelBIC[[val]] <- BIC(model)
    } else {
        print("Failed to find a solution in this iteration. Pass.")
    }
}

# Export
fnOut <- paste0(fn, ".", "k_", k)
wabo %>% saveRDS(paste0(fnOut, ".RDS"))
write.csv(wabo, paste0(fnOut, ".csv"))

print("Finished. Clustering results are exported to RDS and CSV.")

print("BIC values:")
cat(unlist(modelBIC), sep = ",")
cat("\n")

print(paste0("Mean BIC value: ", mean(unlist(modelBIC))))
