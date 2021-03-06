# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from landoapi.phabricator import RevisionStatus
from landoapi.revisions import check_author_planned_changes, check_diff_author_is_known

pytestmark = pytest.mark.usefixtures("docker_env_vars")


def test_check_diff_author_is_known_with_author(phabdouble):
    phab = phabdouble.get_phabricator_client()
    # Adds author information by default.
    d = phabdouble.diff()
    phabdouble.revision(diff=d, repo=phabdouble.repo())

    diff = phab.call_conduit(
        "differential.diff.search",
        constraints={"phids": [d["phid"]]},
        attachments={"commits": True},
    )["data"][0]

    assert check_diff_author_is_known(diff=diff) is None


def test_check_diff_author_is_known_with_unknown_author(phabdouble):
    phab = phabdouble.get_phabricator_client()
    # No commits for no author data.
    d = phabdouble.diff(commits=[])
    phabdouble.revision(diff=d, repo=phabdouble.repo())

    diff = phab.call_conduit(
        "differential.diff.search",
        constraints={"phids": [d["phid"]]},
        attachments={"commits": True},
    )["data"][0]

    assert check_diff_author_is_known(diff=diff) is not None


@pytest.mark.parametrize(
    "status", [s for s in RevisionStatus if s is not RevisionStatus.CHANGES_PLANNED]
)
def test_check_author_planned_changes_changes_not_planned(phabdouble, status):
    phab = phabdouble.get_phabricator_client()
    r = phabdouble.revision(status=status)

    revision = phab.call_conduit(
        "differential.revision.search",
        constraints={"phids": [r["phid"]]},
        attachments={"reviewers": True, "reviewers-extra": True, "projects": True},
    )["data"][0]
    assert check_author_planned_changes(revision=revision) is None


def test_check_author_planned_changes_changes_planned(phabdouble):
    phab = phabdouble.get_phabricator_client()
    r = phabdouble.revision(status=RevisionStatus.CHANGES_PLANNED)

    revision = phab.call_conduit(
        "differential.revision.search",
        constraints={"phids": [r["phid"]]},
        attachments={"reviewers": True, "reviewers-extra": True, "projects": True},
    )["data"][0]
    assert check_author_planned_changes(revision=revision) is not None
