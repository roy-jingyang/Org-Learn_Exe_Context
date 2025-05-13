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
bpic2015 <- read.csv(
    file = fn,
    header = TRUE, 
    encoding = "UTF-8", 
    fileEncoding = "UTF-8-BOM", 
    stringsAsFactors = TRUE
)

# Preprocess data
# load and transform columns
bpic2015 <- bpic2015 %>%
    select(
        "case.Responsible_actor",
        "case.parts_Bouw",
        "case.concept.name",
        "concept.name",
        "subprocess",
        "phase",
        "org.resource",
        "time.timestamp"
    ) %>%
    rename(
        CaseID = "case.concept.name",
        CaseResponsibleActor = "case.Responsible_actor",
        CasePartsBouw = "case.parts_Bouw",
        Activity = "concept.name",
        Subprocess = "subprocess",
        Phase = "phase",
        CompleteTimestamp = "time.timestamp",
        Resource = "org.resource"
    ) %>%
    mutate(
        CaseID = as.factor(CaseID),
        CaseResponsibleActor = as.factor(CaseResponsibleActor),
        CompleteTimestamp = ymd_hms(CompleteTimestamp),
        Resource = as.factor(Resource),
        Activity = as.factor(Activity),
        Subprocess = as.factor(Subprocess),
        Phase = as.factor(Phase),
        Month = as.factor(month(CompleteTimestamp, label = FALSE)),
        Weekday = as.factor(wday(CompleteTimestamp, label = FALSE, week_start = 1))
    )
bpic2015 <- as.data.frame(bpic2015)

# Run clustering with manual loop to store all models
modelBIC <- list()
niter <- 20
for (i in 1:niter) {
    cat(paste0("=== Iter ", i, " ===\n"))
    set.seed(i)
    model <- stepFlexmix(
        formula = . ~ 1,
        data = bpic2015,
        k = k,
        nrep = 5,
        model = list(
            FLXMRmultinom(Resource ~ .),

            FLXMRmultinom(CaseResponsibleActor ~ .),
            FLXMCmvbinary(CasePartsBouw ~ .),

            FLXMRmultinom(Activity ~ .),
            FLXMRmultinom(Subprocess ~ .),
            FLXMRmultinom(Phase ~ .),

            FLXMRmultinom(Month ~ .),
            FLXMRmultinom(Weekday ~ .)
        ),
        control = list(
            verbose = 1,
            tolerance = 1e-06,
            iter.max = 500
        )
    )
    # model = getModel(models, as.character(k))
    newCol <- paste0("ClusterRep", "_", i)
    bpic2015[[newCol]] <- clusters(model)
    val <- paste0("BICRep", "_", i)
    modelBIC[[val]] <- BIC(model)
}

# Export
fnOut <- paste0(fn, ".", "k_", k)
bpic2015 %>% saveRDS(paste0(fnOut, ".RDS"))
write.csv(bpic2015, paste0(fnOut, ".csv"))

print("Finished. Clustering results are exported to RDS and CSV.")

print("BIC values:")
cat(unlist(modelBIC), sep = ",")
cat("\n")

print(paste0("Mean BIC value: ", mean(unlist(modelBIC))))
