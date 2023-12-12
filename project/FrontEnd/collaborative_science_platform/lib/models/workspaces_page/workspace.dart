import 'package:collaborative_science_platform/models/node.dart';
import 'package:collaborative_science_platform/models/user.dart';
import 'package:collaborative_science_platform/models/workspaces_page/entry.dart';

enum WorkspaceStatus {finalized, workable, inReview, published, rejected}

class Workspace {
  int workspaceId;
  String workspaceTitle;
  List<Entry> entries;
  WorkspaceStatus status;
  int numApprovals;
  List<User> contributors;
  List<User> pendingContributors;
  List<Node> references;
  Workspace({
    required this.workspaceId,
    required this.workspaceTitle,
    required this.entries,
    required this.status,
    required this.numApprovals,
    required this.contributors,
    required this.pendingContributors,
    required this.references,
  });

  factory Workspace.fromJson(Map<String, dynamic> jsonString) {
    var entryList = jsonString['workspace_entries'] as List;
    var contributorsList = jsonString['contributors'] as List;
    var pendingContributorsList = jsonString['pending_contributors'] as List;
    var referencesList = jsonString['references'] as List;

    List<Entry> entries = entryList.map((e) => Entry.fromJson(e)).toList();
    List<User> contributors =
        contributorsList.map((e) => User.fromJsonforNodeDetailPage(e)).toList();
    List<User> pendingContributors =
        pendingContributorsList.map((e) => User.fromJsonforNodeDetailPage(e)).toList();
    List<Node> references = referencesList.map((e) => Node.fromJsonforNodeDetailPage(e)).toList();

    String statusString = jsonString['status'];
    WorkspaceStatus status = (statusString == "finalized") ? WorkspaceStatus.finalized
        : (statusString == "workable") ? WorkspaceStatus.workable
        : (statusString == "in_review") ? WorkspaceStatus.inReview
        : (statusString == "published") ? WorkspaceStatus.published
        : WorkspaceStatus.rejected;

    return Workspace(
        workspaceId: jsonString['workspace_id'],
        workspaceTitle: jsonString['workspace_title'],
        entries: entries,
        status: status,
        numApprovals: jsonString['num_approvals'],
        contributors: contributors,
        pendingContributors: pendingContributors,
        references: references);
  }
}