#!/usr/bin/env bash
# Shows how two clones claim ID numbers from one counter ref on a shared remote.
#
# The counter ref points at a parentless claim commit on the empty tree. Its
# message holds one line per prefix (ST=0003) and a random token. A claim reads
# the commit, raises one line, and pushes a new claim commit with a lease on the
# old SHA. A rejected push waits a random 0.1 to 1 second and starts again.
#
# Usage:
#   ref-claim-race.sh [rounds]                 local bare remote, default 20 rounds
#   ref-claim-race.sh [rounds] <remote URL>    for example a GitHub repository
#
# With a remote URL, the script uses a ref name unique to this run and deletes
# that ref at the end. It never touches refs/ids/counters itself.
set -u
ROUNDS=${1:-20}
REMOTE_URL=${2:-}
MAX_TRIES=10

S=$(mktemp -d)
cd "$S" || exit 1
git init -q a
git init -q b
if [ -n "$REMOTE_URL" ]; then
  REMOTE=$REMOTE_URL
  REF=refs/ids/race-test-$(date +%s)-$$
else
  git init -q --bare remote.git
  REMOTE=$S/remote.git
  REF=refs/ids/counters
fi

cleanup() {
  if [ -n "$REMOTE_URL" ]; then
    if git -C a push -q "$REMOTE" ":$REF" 2>/dev/null; then
      echo "Cleanup: deleted $REF on the remote."
    else
      echo "Cleanup: could not delete $REF on the remote. Delete it by hand."
    fi
  fi
  rm -rf "$S"
}
trap cleanup EXIT

short() { printf '%.7s' "$1"; }
token() { od -An -N8 -tx8 /dev/urandom | tr -d ' '; }

# Creates a claim commit in <clone> with <message> and prints its SHA.
claim_commit() { # <clone> <message>
  local tree
  tree=$(git -C "$1" mktree </dev/null)
  printf '%s\n' "$2" | git -C "$1" commit-tree "$tree"
}

# Pushes <sha> to the counter ref with a lease on <old sha>. An empty old SHA
# means create-only. Prints git's porcelain flag: '*' or '+' updated, '!' rejected.
push_lease() { # <clone> <sha> <old sha>
  git -C "$1" push --porcelain --verbose --force-with-lease="$REF:$3" "$REMOTE" "$2:$REF" 2>&1 |
    grep -P '^[*!=+\- ]\t' | head -1 | cut -f1,3
}

# Fetches the counter ref into <clone>. Prints its SHA, or nothing if missing.
read_ref() { # <clone>
  git -C "$1" fetch -q "$REMOTE" "+$REF:$REF" 2>/dev/null || return 0
  git -C "$1" rev-parse "$REF"
}

# Claims the next number of <prefix> from <clone>. Logs each attempt to
# log.<clone>.<round> and prints the claimed ID, or nothing on failure.
claim() { # <clone> <prefix> <round>
  local clone=$1 prefix=$2 log=log.$1.$3 try old body current next msg new result flag
  for try in $(seq 1 "$MAX_TRIES"); do
    old=$(read_ref "$clone")
    if [ -z "$old" ]; then
      echo "    $clone try $try: $REF is missing, claim fails" >>"$log"
      return
    fi
    body=$(git -C "$clone" log -1 --format=%B "$old")
    current=$(printf '%s\n' "$body" | sed -n "s/^$prefix=//p")
    next=$(printf '%04d' $((10#${current:-0} + 1)))
    msg=$(printf '%s\n' "$body" | grep -v -e "^$prefix=" -e '^token=' -e '^$'
      echo "$prefix=$next"
      echo "token=$(token)")
    msg=$(printf '%s\n' "$msg" | sort)
    new=$(claim_commit "$clone" "$msg")
    result=$(push_lease "$clone" "$new" "$old")
    flag=${result%%$'\t'*}
    if [ "$flag" = "*" ] || [ "$flag" = "+" ]; then
      echo "    $clone try $try: read $prefix=${current:-none} at $(short "$old"), pushed $prefix=$next as $(short "$new") -> accepted" >>"$log"
      echo "$prefix-$next"
      return
    fi
    wait_s=$(printf '0.%d' $((RANDOM % 9 + 1)))
    echo "    $clone try $try: read $prefix=${current:-none} at $(short "$old"), pushed $prefix=$next as $(short "$new") -> rejected ${result#*$'\t'}, retry in ${wait_s}s" >>"$log"
    sleep "$wait_s"
  done
  echo "    $clone: gave up after $MAX_TRIES rejections" >>"$log"
}

echo "Remote: ${REMOTE_URL:-local bare repository in $S}"
echo "Counter ref: $REF"
echo

echo "== Part 1: seed =="
seed_msg=$(printf 'FAGAN=0000\nST=0000\ntoken=%s' "$(token)")
seed_sha=$(claim_commit a "$seed_msg")
result=$(push_lease a "$seed_sha" "")
echo "  a creates $REF at $(short "$seed_sha") with ST=0000 and FAGAN=0000 -> git flag '${result%%$'\t'*}'"
if [ -z "$(read_ref a)" ]; then
  echo "  Seed failed. Check the remote URL and your push rights."
  exit 1
fi
echo

echo "== Part 2: race, $ROUNDS rounds =="
echo "In each round, a and b claim at the same moment."
echo "Odd rounds: both claim ST. Even rounds: a claims ST, b claims FAGAN."
echo
: >ids
for i in $(seq 1 "$ROUNDS"); do
  pb=ST
  [ $((i % 2)) -eq 0 ] && pb=FAGAN
  claim a ST "$i" >"id.a.$i" &
  claim b "$pb" "$i" >"id.b.$i" &
  wait
  ida=$(cat "id.a.$i")
  idb=$(cat "id.b.$i")
  echo "Round $i: a got ${ida:-nothing}, b got ${idb:-nothing}"
  cat "log.a.$i" "log.b.$i" 2>/dev/null
  echo "$ida" >>ids
  echo "$idb" >>ids
done
echo

echo "== Part 3: check =="
failed=$(grep -c '^$' ids)
dups=$(grep -v '^$' ids | sort | uniq -d)
claimed=$(grep -cv '^$' ids)
st_count=$(grep -c '^ST-' ids)
fagan_count=$(grep -c '^FAGAN-' ids)
final=$(git -C a log -1 --format=%B "$(read_ref a)" | grep -v '^token=' | grep -v '^$' | tr '\n' ' ')
echo "  IDs handed out: $claimed, failed claims: $failed"
echo "  Duplicate IDs: ${dups:-none}"
echo "  Claim commit on the remote: $final"
echo "  Expected: ST=$(printf %04d "$st_count") FAGAN=$(printf %04d "$fagan_count")"
if [ -z "$dups" ] && [ "$failed" -eq 0 ] &&
  [ "$final" = "FAGAN=$(printf %04d "$fagan_count") ST=$(printf %04d "$st_count") " ]; then
  echo "  Result: OK, no number was handed out twice and no number was skipped."
else
  echo "  Result: FAIL"
fi
echo

echo "== Part 4: why each claim commit needs a token =="
echo "a pushes the SHA that $REF already holds, with a lease on an older SHA."
cur=$(read_ref a)
result=$(push_lease a "$cur" "$seed_sha")
echo "  git flag '${result%%$'\t'*}' ${result#*$'\t'}"
echo "  A push of the same SHA is not rejected. Two callers with identical claim"
echo "  commits would both believe they won, so every claim commit gets a token."
